from marshmallow import Schema, fields, validate

class ApplicationSchema(Schema):
    id = fields.Int(dump_only=True)
    job_id = fields.Int(required=True)
    student_id = fields.Int(required=True)
    status = fields.Str(
        validate=validate.OneOf(['pending', 'analysis', 'interview', 'accepted', 'rejected']),
        missing='pending'
    )
    cover_letter = fields.Str(allow_none=True, validate=validate.Length(max=2000))
    created_at = fields.DateTime(dump_only=True)
    
    # Nested fields for related data
    job = fields.Nested('JobSchema', dump_only=True, exclude=['applications'])
    student = fields.Nested('StudentSchema', dump_only=True, exclude=['applications'])

class ApplicationStatusUpdateSchema(Schema):
    status = fields.Str(
        required=True,
        validate=validate.OneOf(['pending', 'analysis', 'interview', 'accepted', 'rejected'])
    )

class ApplyToJobSchema(Schema):
    cover_letter = fields.Str(allow_none=True, validate=validate.Length(max=2000))
